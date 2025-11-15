const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('nick')
        .setDescription('Bir kullanıcının takma adını değiştirir.')
        .addUserOption(option =>
            option.setName('member')
                .setDescription('Takma adı değiştirilecek kullanıcı')
                .setRequired(true))
        .addStringOption(option =>
            option.setName('new_nick')
                .setDescription('Yeni takma ad')
                .setRequired(true))
        .setDefaultMemberPermissions(PermissionFlagsBits.ManageNicknames),
    async execute(interaction) {
        const member = interaction.options.getMember('member');
        const newNick = interaction.options.getString('new_nick');

        if (!member) {
            return await interaction.reply({ content: '❌ Kullanıcı bulunamadı.', ephemeral: true });
        }

        try {
            const oldNick = member.displayName;
            await member.setNickname(newNick);
            await interaction.reply(`✅ ${member} kullanıcısının takma adı **${oldNick}** → **${newNick}** olarak değiştirildi.`);
        } catch (error) {
            console.error('Nick error:', error);
            await interaction.reply({ content: '❌ Takma ad değiştirilemedi.', ephemeral: true });
        }
    }
};
