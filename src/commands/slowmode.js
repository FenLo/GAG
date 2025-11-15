const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('slowmode')
        .setDescription('Kanalda yavaş mod süresi ayarlar (saniye cinsinden).')
        .addIntegerOption(option =>
            option.setName('seconds')
                .setDescription('Yavaş mod süresi (saniye cinsinden)')
                .setRequired(true)
                .setMinValue(0)
                .setMaxValue(21600))
        .setDefaultMemberPermissions(PermissionFlagsBits.ManageChannels),
    async execute(interaction) {
        const seconds = interaction.options.getInteger('seconds');

        try {
            await interaction.channel.setRateLimitPerUser(seconds);
            
            if (seconds === 0) {
                await interaction.reply('✅ Yavaş mod kapatıldı.');
            } else {
                await interaction.reply(`🕐 Yavaş mod ${seconds} saniyeye ayarlandı.`);
            }
        } catch (error) {
            console.error('Slowmode error:', error);
            await interaction.reply({ content: '❌ Yavaş mod ayarlanamadı.', ephemeral: true });
        }
    }
};
