const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');
const { setAutorole } = require('../database');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('otorol')
        .setDescription('Sunucuya yeni katılanlar için otomatik rol ayarlar.')
        .addRoleOption(option =>
            option.setName('user_role')
                .setDescription('Kullanıcılar için rol')
                .setRequired(true))
        .addRoleOption(option =>
            option.setName('bot_role')
                .setDescription('Botlar için rol')
                .setRequired(true))
        .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    async execute(interaction) {
        const userRole = interaction.options.getRole('user_role');
        const botRole = interaction.options.getRole('bot_role');

        if (!userRole || !botRole) {
            return await interaction.reply({ content: '❌ Roller bulunamadı.', ephemeral: true });
        }

        setAutorole(
            interaction.guild.id,
            interaction.guild.name,
            userRole.id,
            botRole.id
        );

        await interaction.reply({
            content: `✅ Otomatik roller güncellendi! Kullanıcılar için ${userRole}, botlar için ${botRole} atanacak.`,
            ephemeral: true
        });
    }
};
